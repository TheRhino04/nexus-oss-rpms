Summary: Nexus manages software “artifacts” required for development, deployment, and provisioning.
Name: nexus
Version: 2.7.0
Release: 2
License: AGPL
Group: unknown
URL: http://nexus.sonatype.org/
Source0: %{name}-%{version}-bundle.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: java-openjdk >= 1:1.7.0
AutoReqProv: no
Patch0:ret_code.patch

%define __os_install_post %{nil}
%define debug_package %{nil}

%description
A package repository

%prep
%setup -q -n %{name}-%{version}-05

%patch0 -p1

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/%{name}
mv * $RPM_BUILD_ROOT/usr/share/%{name}

arch=$(echo "%{_arch}" | sed -e 's/_/-/')
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
cd $RPM_BUILD_ROOT/etc/init.d/
ln -sf /usr/share/%{name}/bin/nexus $RPM_BUILD_ROOT/etc/init.d/nexus

# patch work dir
sed -i -e 's#nexus-work=.*#nexus-work=/var/lib/nexus/#g' $RPM_BUILD_ROOT/usr/share/%{name}/conf/nexus.properties
mkdir -p $RPM_BUILD_ROOT/var/lib/nexus

# patch tcp port
sed -i -e 's#application-port=.*#application-port=80#g' $RPM_BUILD_ROOT/usr/share/%{name}/conf/nexus.properties

#patch properties file
mkdir -p $RPM_BUILD_ROOT/etc/nexus
mv $RPM_BUILD_ROOT/usr/share/%{name}/conf/* $RPM_BUILD_ROOT/etc/nexus
rm -rf $RPM_BUILD_ROOT/usr/share/%{name}/conf
ln -sd /etc/nexus $RPM_BUILD_ROOT/usr/share/%{name}/conf

# patch pid dir
sed -i -e 's#PIDDIR=.*#PIDDIR=/var/run/nexus#' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus
mkdir -p $RPM_BUILD_ROOT/var/run/nexus

#patch user to run
sed -i -e 's/#RUN_AS_USER=/RUN_AS_USER=nexus/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus

# patch logs dir and logfile
mkdir -p $RPM_BUILD_ROOT/var/log/nexus
rm -rf $RPM_BUILD_ROOT/usr/share/%{name}/logs
ln -sd /var/log/nexus $RPM_BUILD_ROOT/usr/share/%{name}/logs
sed -i -e 's#wrapper.logfile=.*#wrapper.logfile=/var/log/nexus/nexus.log#' $RPM_BUILD_ROOT/usr/share/%{name}/bin/jsw/conf/wrapper.conf

#add logrotate configuration
mkdir -p $RPM_BUILD_ROOT/etc/logrotate.d
cat > $RPM_BUILD_ROOT/etc/logrotate.d/nexus << "EOF"
/var/log/nexus/*.log {
    copytruncate
    weekly
    rotate 52
    compress
    missingok
    create 0644 nexus nexus
}
EOF

%pre
/usr/sbin/groupadd -r nexus &>/dev/null || :
# SUSE version had -o here, but in Fedora -o isn't allowed without -u
/usr/sbin/useradd -g nexus -s /bin/false -r -c "Nexus Repository Management server" \
-d "/var/lib/nexus" nexus &>/dev/null || :

%post
/sbin/chkconfig --add nexus

%preun
if [ "$1" = 0 ] ; then
    # if this is uninstallation as opposed to upgrade, delete the service
    /sbin/service nexus stop > /dev/null 2>&1
    /sbin/chkconfig --del nexus
fi

%postun
if [ "$1" -ge 1 ]; then
    /sbin/service nexus condrestart > /dev/null 2>&1
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,nexus,nexus,-)
%attr(-,root,root) /etc/init.d/nexus
%doc
/usr/share/%{name}
/var/lib/nexus
/var/run/nexus
/var/log/nexus
%config(noreplace) /etc/nexus
/etc/logrotate.d/nexus

%changelog
* Thu Dec 22 2011 Jens Braeuer <braeuer.jens@googlemail.com> - 1.9.2.3-1
- Initial packaging.
- For now nexus will run as root and listen to port 80

