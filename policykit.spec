%define lib_major 2
%define libname %mklibname polkit %{lib_major}
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

Summary: Authorization Toolkit
Name: policykit
Version: 0.9
Release: %mkrel 10
License: MIT
Group: System/Libraries
URL: https://people.freedesktop.org/~david/polkit-spec.html
Source0: http://hal.freedesktop.org/releases/PolicyKit-%{version}.tar.gz
# (fc) 0.9-3mdv adapt to ConsoleKit 0.3 API (Fedora)
Patch0: pk-ck-api-change.patch
# (fc) fix memleak (Fedora)
Patch1: entry-leak.patch
# (fc) fix default D-Bus policy (fdo bug #18948)
Patch2: polkit-0.8-dbus-policy.patch
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
BuildRequires: perl-XML-Parser
BuildRequires: intltool

%description
PolicyKit is a toolkit for defining and handling authorizations.
It is used to allows unprivileged processes to speak to 
privileged processes.

%package -n %{libname}
Summary: Authorization Toolkit
Group: System/Libraries
Requires: dbus >= %{dbus_version}
Requires: dbus-glib >= %{dbus_glib_version}
Requires: glib2 >= %{glib2_version}
Requires: ConsoleKit >= %{consolekit_version}
Requires: pam >= %{pam_version}
Requires: %{name} = %{version}-%{release}

%description -n %{libname}
PolicyKit is a toolkit for defining and handling authorizations.
It is used to allows unprivileged processes to speak to 
privileged processes.

%package -n %{libnamedevel}
Summary: Headers and libraries for PolicyKit
Group: Development/C
Requires: %{libname} = %{version}-%{release}
Requires: pkgconfig
Requires: glib2-devel
Requires: dbus-devel
Provides: polkit-devel = %{version}-%{release}

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
%patch0 -p1 -b .ck03
%patch1 -p1 -b .entry-leak
%patch2 -p1 -b .policy-fix

%build
%configure2_5x --disable-selinux

#parallel build is broken
make

%install
rm -rf %{buildroot}
%makeinstall_std profiledir=%{_sysconfdir}/bash_completion.d

rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_libdir}/*.a

# standard completion file name
mv %{buildroot}%{_sysconfdir}/bash_completion.d/polkit-bash-completion.sh \
   %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}
chmod 644 %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}

%clean
rm -rf %{buildroot}

%pre
%_pre_useradd polkituser / /sbin/nologin %{polkit_uid}

%postun
%_postun_userdel polkituser

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root,-)

%doc AUTHORS COPYING HACKING NEWS README doc/TODO

%config(noreplace) %{_sysconfdir}/pam.d/polkit
%dir %{_sysconfdir}/PolicyKit
%config(noreplace) %{_sysconfdir}/PolicyKit/PolicyKit.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.PolicyKit.conf
%{_sysconfdir}/bash_completion.d/%{name}

%{_bindir}/*
%{_libexecdir}/polkitd

%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

# see README file for why these permissions are necessary
%attr(4755,polkituser,root) %{_libexecdir}/polkit-set-default-helper
%attr(2755,root,polkituser) %{_libexecdir}/polkit-read-auth-helper
%attr(2755,root,polkituser) %{_libexecdir}/polkit-revoke-helper
%attr(2755,root,polkituser) %{_libexecdir}/polkit-explicit-grant-helper
%attr(2755,root,polkituser) %{_libexecdir}/polkit-grant-helper
%attr(4754,root,polkituser) %{_libexecdir}/polkit-grant-helper-pam
%attr(4755,root,polkituser) %{_libexecdir}/polkit-resolve-exe-helper
%attr(0770,root,polkituser) %dir %{_localstatedir}/run/PolicyKit
%attr(0770,root,polkituser) %dir %{_localstatedir}/lib/PolicyKit
%attr(0755,polkituser,root) %dir %{_localstatedir}/lib/PolicyKit-public
%attr(0664,polkituser,polkituser) %{_localstatedir}/lib/misc/PolicyKit.reload

%dir %{_datadir}/PolicyKit
%dir %{_datadir}/PolicyKit/policy
%{_datadir}/PolicyKit/config.dtd
%{_datadir}/PolicyKit/policy/org.freedesktop.policykit.policy

%{_datadir}/dbus-1/system-services/org.freedesktop.PolicyKit.service
%{_datadir}/dbus-1/interfaces/org.freedesktop.PolicyKit.AuthenticationAgent.xml

%files -n %{libname}
%defattr(-,root,root,-)
%{_libdir}/lib*.so.%{lib_major}*

%files -n %{libnamedevel}
%defattr(-,root,root,-)
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*

%files docs
%defattr(-,root,root,-)
%{_datadir}/gtk-doc/html/polkit



%changelog
* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 0.9-9mdv2011.0
+ Revision: 667797
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.9-8mdv2011.0
+ Revision: 607188
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0.9-7mdv2010.1
+ Revision: 523693
- rebuilt for 2010.1

* Wed Aug 26 2009 Frederic Crozat <fcrozat@mandriva.com> 0.9-6mdv2010.0
+ Revision: 421497
- Patch1 (Fedora): fix memleak
- Patch2 (Fedora): fix default D-Bus policy (fdo bug #18948)

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 0.9-5mdv2009.1
+ Revision: 351646
- rebuild

* Wed Sep 10 2008 Frederic Crozat <fcrozat@mandriva.com> 0.9-4mdv2009.0
+ Revision: 283600
- bump release
- Fix permission on reload file, was preventing revocation / monitoring

* Tue Aug 12 2008 Frederic Crozat <fcrozat@mandriva.com> 0.9-3mdv2009.0
+ Revision: 271194
- Patch0 (Fedora): adapt to ConsoleKit 0.3 API

* Wed Jul 23 2008 Frederic Crozat <fcrozat@mandriva.com> 0.9-2mdv2009.0
+ Revision: 242565
- Fix buildrequires
- Release 0.9
- Fix some files permissions
- Disable parallel build

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Thu May 22 2008 Frederic Crozat <fcrozat@mandriva.com> 0.8-2mdv2009.0
+ Revision: 210081
- Fix files permissions / mode (from Fedora) (Mdv bug #40896)

* Tue May 06 2008 Götz Waschk <waschk@mandriva.org> 0.8-1mdv2009.0
+ Revision: 201947
- new version
- drop patch
- update file list

* Tue Feb 26 2008 Colin Guthrie <cguthrie@mandriva.org> 0.7-5mdv2008.1
+ Revision: 175634
- Better fix for policy files on xfs/reiserfs from upstream (mdv#36043)

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Dec 12 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.7-4mdv2008.1
+ Revision: 119064
- no .sh extension, and no executable bit for bash completion file

* Tue Dec 11 2007 Frederic Crozat <fcrozat@mandriva.com> 0.7-3mdv2008.1
+ Revision: 117312
- Fix permissions/ownership on pam helper
- Add comment for patch

* Tue Dec 11 2007 Colin Guthrie <cguthrie@mandriva.org> 0.7-2mdv2008.1
+ Revision: 117086
- Fix #36043. PolicyKit failed to read .policy files on XFS filesystems

* Thu Dec 06 2007 Frederic Crozat <fcrozat@mandriva.com> 0.7-1mdv2008.1
+ Revision: 115894
- Fix BuildRequires
- Release 0.7
- Clean specfile

* Mon Dec 03 2007 Frederic Crozat <fcrozat@mandriva.com> 0.6-4mdv2008.1
+ Revision: 114607
- Fix devel provide

* Fri Nov 30 2007 Frederic Crozat <fcrozat@mandriva.com> 0.6-3mdv2008.1
+ Revision: 114077
- Remove dependency on selinux, we don't use it

* Sat Nov 10 2007 David Walluck <walluck@mandriva.org> 0.6-2mdv2008.1
+ Revision: 107418
- rebuild
- 0.6

* Mon Sep 03 2007 David Walluck <walluck@mandriva.org> 0.5-2mdv2008.0
+ Revision: 78593
- Import policykit

