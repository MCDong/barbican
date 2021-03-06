%define version BUILD_VERSION
%define release 1

Summary: Common files for Barbican Key Manager
Name: barbican-common
Version: %{version}
Release: %{release}
Source0: barbican-%{version}.tar.gz
Vendor: Rackspace, Inc.
Packager: Douglas Mendizabal <douglas.mendizabal@rackspace.com>
Url: http://github.com/cloudkeep/barbican
License: Apache License (2.0)
Group: Python WSGI Application
BuildRoot: %{_tmppath}/barbican-%{version}-%{release}-buildroot
BuildArch: noarch
BuildRequires: python2-devel
Requires(pre): shadow-utils
#TODO(dmend): add python-cryptography once it's available
Requires: python-alembic, python-babel, python-crypto
Requires: python-eventlet, python-iso8601, python-jsonschema
Requires: python-keystonemiddleware, python-kombu, python-netaddr
Requires: python-oslo-config, python-oslo-messaging
Requires: python-paste, python-paste-deploy, python-pbr, python-pecan
Requires: python-six, python-sqlalchemy, python-stevedore
Requires: python-webob

%description
Common files for Barbican Key Management API (barbican-api),
Barbican Worker (barbican-worker) and Barbican Keystone Listener
(barbican-keystone-listener)

%prep
%setup -n barbican-%{version} -q

%build
python setup.py build

%install
python setup.py install -O1 --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/init
mkdir -p $RPM_BUILD_ROOT/etc/barbican/vassals
mkdir -p $RPM_BUILD_ROOT/var/l{ib,og}/barbican
install -m 644 etc/barbican/policy.json $RPM_BUILD_ROOT/etc/barbican
install -m 644 etc/init/barbican.conf $RPM_BUILD_ROOT/etc/init
install -m 644 etc/init/barbican-worker.conf $RPM_BUILD_ROOT/etc/init
install -m 644 etc/init/barbican-keystone-listener.conf $RPM_BUILD_ROOT/etc/init
install bin/barbican-worker.py $RPM_BUILD_ROOT/usr/bin
install bin/barbican-keystone-listener.py $RPM_BUILD_ROOT/usr/bin
install bin/barbican-db-manage.py $RPM_BUILD_ROOT/usr/bin
install -m 644 -D etc/barbican/barbican* $RPM_BUILD_ROOT/etc/barbican
install -m 644 -D etc/barbican/vassals/*.ini $RPM_BUILD_ROOT/etc/barbican/vassals
touch $RPM_BUILD_ROOT/var/log/barbican/barbican-api.log

# install log rotation
mkdir -p $RPM_BUILD_ROOT/etc/logrotate.d
install -m644 etc/logrotate.d/barbican-api $RPM_BUILD_ROOT/etc/logrotate.d/barbican-api

%pre
# Add the 'barbican' user
getent group barbican >/dev/null || groupadd -r barbican
getent passwd barbican >/dev/null || \
    useradd -r -g barbican -d /var/lib/barbican -s /sbin/nologin \
    -c "Barbican Key Manager user account." barbican
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,barbican,barbican)
%{python_sitelib}/*
%dir /var/lib/barbican


# ------------------
# API package
# ------------------
%package -n barbican-api
Summary: Barbican Key Manager API daemon
Requires: barbican-common

%description -n barbican-api
Barbican Key Manager API daemon

%files -n barbican-api
%defattr(-,root,root)
%verify(not md5 size mtime) %attr(0750, barbican,root) /var/log/barbican/barbican-api.log
/etc/logrotate.d/barbican-api
%attr(0755,root,root) /usr/bin/barbican.sh
%attr(0755,root,root) /usr/bin/barbican-db-manage.py
%config(noreplace) /etc/init/barbican.conf
%config(noreplace) /etc/barbican/*

%preun -n barbican-api
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /sbin/stop barbican-api >/dev/null 2>&1 || :
fi


# ------------------
# Worker package
# ------------------
%package -n barbican-worker
Summary: Barbican Key Manager worker daemon
Requires: barbican-common

%description -n barbican-worker
Barbican Key Manager worker daemon

%files -n barbican-worker
%defattr(-,root,root)
%dir /var/lib/barbican
%verify(not md5 size mtime) %attr(0750, barbican,root) /var/log/barbican/barbican-api.log
/etc/logrotate.d/barbican-api
%attr(0755,root,root) /usr/bin/barbican-worker.py
%attr(0755,root,root) /usr/bin/barbican-db-manage.py
%config(noreplace) /etc/init/barbican-worker.conf
%config(noreplace) /etc/barbican/*

%preun -n barbican-worker
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /sbin/stop barbican-worker >/dev/null 2>&1 || :
fi


# -------------------------
# Keystone Listener package
# -------------------------
%package -n barbican-keystone-listener
Summary: Barbican Keystone Listener daemon
Requires: barbican-common

%description -n barbican-keystone-listener
Barbican Keystone Listener daemon

%files -n barbican-keystone-listener
%defattr(-,root,root)
%dir /var/lib/barbican
%verify(not md5 size mtime) %attr(0750, barbican,root) /var/log/barbican/barbican-keystone-listener.log
/etc/logrotate.d/barbican-api
%attr(0755,root,root) /usr/bin/barbican-keystone-listener.py
%attr(0755,root,root) /usr/bin/barbican-db-manage.py
%config(noreplace) /etc/init/barbican-keystone-listener.conf
%config(noreplace) /etc/barbican/*

%preun -n barbican-keystone-listener
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /sbin/stop barbican-keystone-listener >/dev/null 2>&1 || :
fi
