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

%define __os_install_post %{nil}

%description
A package repository

%prep
%setup -q -n %{name}-%{version}-05

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

# patch pid dir
sed -i -e 's#PIDDIR=.*#PIDDIR=/var/run/#' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus

#patch user to run
sed -i -e 's/#RUN_AS_USER=/RUN_AS_USER=nexus/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus

# patch logfile
mkdir -p $RPM_BUILD_ROOT/var/log/nexus
sed -i -e 's#wrapper.logfile=.*#wrapper.logfile=/var/log/nexus/nexus.log#' $RPM_BUILD_ROOT/usr/share/%{name}/bin/jsw/conf/wrapper.conf

%pre
id -u nexus &>/dev/null || /usr/sbin/useradd -r -c "Nexus server user" -d /var/lib/nexus nexus

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,nexus,nexus,-)
%attr(-,root,root) /etc/init.d/nexus
%doc
/usr/share/%{name}
/var/lib/nexus
/var/log/nexus

%changelog
* Thu Dec 22 2011 Jens Braeuer <braeuer.jens@googlemail.com> - 1.9.2.3-1
- Initial packaging.
- For now nexus will run as root and listen to port 80

