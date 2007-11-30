%define libname %mklibname polkit 2
%define libnamedevel %mklibname polkit -d

%define _localstatedir %{_var}

%define expat_version           1.95.5
%define glib2_version           2.6.0
%define dbus_version            0.90
%define dbus_glib_version	0.70
%define gtk_doc_version         1.4
%define consolekit_version      0.2.1
%define pam_version             0.99.6

# uid/gid allocated in this bug:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=244950
%define polkit_uid              87

Summary: Toolkit for privilege control
Name: policykit
Version: 0.6
Release: %mkrel 3
License: AFL/GPL
Group: System/Libraries
URL: http://people.freedesktop.org/~david/polkit-spec.html
Source0: http://hal.freedesktop.org/releases/PolicyKit-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Obsoletes: PolicyKit < %{version}-%{release}
Provides: PolicyKit = %{version}-%{release}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires: expat-devel >= %{expat_version}
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: dbus-devel  >= %{dbus_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: gtk-doc >= %{gtk_doc_version}
BuildRequires: xmlto
BuildRequires: pam-devel >= %{pam_version}

%description
PolicyKit is a toolkit for defining and handling the policy that
allows unprivileged processes to speak to privileged processes.

%package -n %{libname}
Summary: Toolkit for privilege control
Group: System/Libraries
Requires: dbus >= %{dbus_version}
Requires: dbus-glib >= %{dbus_glib_version}
Requires: glib2 >= %{glib2_version}
Requires: ConsoleKit >= %{consolekit_version}
Requires: pam >= %{pam_version}
Requires: %{name} = %{version}-%{release}

%description -n %{libname}
PolicyKit is a toolkit for defining and handling the policy that
allows unprivileged processes to speak to privileged processes.

%package -n %{libnamedevel}
Summary: Headers and libraries for PolicyKit
Group: Development/C
Requires: %{libname} = %{version}-%{release}
Requires: pkgconfig
Requires: glib2-devel
Requires: dbus-devel
Provides: pokit-devel = %{version}-%{release}

%description -n %{libnamedevel}
Headers and libraries for PolicyKit.

%package docs
Summary: Documentation for PolicyKit
Group: Development/C
Requires: %{name} = %{version}-%{release}
# stupid guidelines require this for ownership of /usr/share/gtk-doc
Requires: gtk-doc

%description docs
Documentation for PolicyKit.

%prep
%setup -q -n PolicyKit-%{version}

%build
%{configure2_5x} --docdir=%{_docdir}/%{name} --enable-docbook-docs --disable-man-pages --disable-selinux
%{make}

%install
rm -rf %{buildroot}
%{makeinstall_std}

rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_libdir}/*.a

%clean
rm -rf %{buildroot}

%pre
%_pre_useradd polkituser / /sbin/nologin %{polkit_uid}

%postun
%_postun_userdel polkituser

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%files
%defattr(-,root,root,-)

%doc AUTHORS COPYING HACKING NEWS README doc/TODO

%config(noreplace) %{_sysconfdir}/pam.d/polkit
%dir %{_sysconfdir}/PolicyKit
%config(noreplace) %{_sysconfdir}/PolicyKit/PolicyKit.conf

%{_bindir}/*
#%{_libexecdir}/*


#%{_mandir}/man1/*
#%{_mandir}/man5/*
#%{_mandir}/man8/*

# see upstream design specification for why these permissions are necessary
%attr(2755,root,polkituser) %{_libexecdir}/polkit-grant-helper
%attr(4755,root,root) %{_libexecdir}/polkit-grant-helper-pam
%attr(0775,polkituser,polkituser) %dir %{_localstatedir}/run/PolicyKit
%attr(0775,polkituser,polkituser) %dir %{_localstatedir}/lib/PolicyKit
#%attr(0644,root,root) %{_localstatedir}/lib/PolicyKit/reload

%dir %{_datadir}/PolicyKit
%dir %{_datadir}/PolicyKit/policy
%{_datadir}/PolicyKit/config.dtd

%files -n %{libname}
%defattr(-,root,root,-)

%{_libdir}/lib*.so.*

%files -n %{libnamedevel}
%defattr(-,root,root,-)

%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*

%files docs
%defattr(-,root,root,-)

#%doc %dir %{_docdir}/%{name}/spec
#%doc %{_docdir}/%{name}/spec/*

%dir %{_datadir}/gtk-doc/html/polkit
%{_datadir}/gtk-doc/html/polkit/*

#%dir %{_datadir}/gtk-doc/html/polkit-dbus
#%{_datadir}/gtk-doc/html/polkit-dbus/*

#%dir %{_datadir}/gtk-doc/html/polkit-grant
#%{_datadir}/gtk-doc/html/polkit-grant/*

%changelog
