%define name opencbm
%define ver 0.4.2a
%define major 0
%define libname %mklibname %name %major
Summary: OPENCBM/CBM4Linux kernel module, runtime libraries and utilities
Name: %{name}
Version: %ver
Release: %mkrel 1
Group: System/Kernel and hardware
License: GPL
Source: http://downloads.sourceforge.net/opencbm/%{name}-%{ver}-src.zip
Patch1: opencbm-0.4.2-pic.patch
Buildroot: %_tmppath/%{name}
Url: http://www.lb.shuttle.de/puffin/cbm4linux
BuildRequires: kernel-source
BuildRequires: linuxdoc-tools
#gw missing dep in linuxdoc-tools
BuildRequires: texinfo
Requires: dkms-%name = %version

%description
The opencbm (cbm4linux) package is a linux kernel module and a few user space
support programs to control and use serial devices as used by most Commodore
(CBM) 8-bit machines, such as disk drives and printers from your trusty C64.  A
fast .d64 transfer program is included.

%package -n %libname
Summary: Shared library of OPENCBM/CBM4Linux
Group: System/Libraries

%description -n %libname
The opencbm (cbm4linux) package is a linux kernel module and a few user space
support programs to control and use serial devices as used by most Commodore
(CBM) 8-bit machines, such as disk drives and printers from your trusty C64.  A
fast .d64 transfer program is included.


%package -n %libname-devel
Summary: OPENCBM/CBM4Linux linktime libraries and header files
Group: Development/C
Requires: %{libname} = %{version}
Provides: lib%name-devel = %version-%release

%description -n %libname-devel
Libraries and header files for opencbm/cbm4linux.

%package -n dkms-%name
Summary:	DKMS-ready opencbm/cbm4linux driver
Group:		Development/Kernel
Requires(pre):	dkms
Requires(post): dkms

%description -n dkms-%name
The opencbm (cbm4linux) package is a linux kernel module and a few
user space support programs to control and use serial devices as used
by most Commodore (CBM) 8-bit machines, such as disk drives and
printers from your trusty C64.  A fast .d64 transfer program is
included.


%prep
%setup -q -n %name-%version
%patch1 -p1

%build
make -f LINUX/Makefile

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %buildroot/%_sysconfdir/udev/rules.d
make -f LINUX/Makefile install-files \
	PREFIX=$RPM_BUILD_ROOT/%{_prefix} \
	BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
	LIBDIR=$RPM_BUILD_ROOT/%{_libdir} \
	MANDIR=$RPM_BUILD_ROOT/%{_mandir}/man1 \
	INFODIR=$RPM_BUILD_ROOT/%{_infodir} \
	INCDIR=$RPM_BUILD_ROOT/%{_includedir} \
	UDEV_RULES=%buildroot/%_sysconfdir/udev/rules.d \
	MODDIR=$RPM_BUILD_ROOT/"`for d in /lib/modules/\`uname -r\`/{extra,misc,kernel/drivers/char}; do test -d $d && echo $d; done | head -n 1`"
rm -rf %buildroot/lib/modules %buildroot/cbm.ko

mkdir -p %{buildroot}%{_usrsrc}/%name-%version-%release/sys
cp -r sys/linux/ %{buildroot}%{_usrsrc}/%name-%version-%release/sys
cp -r include/LINUX/* %{buildroot}%{_usrsrc}/%name-%version-%release/sys/linux
cp -r LINUX %{buildroot}%{_usrsrc}/%name-%version-%release
cd %{buildroot}%{_usrsrc}/%name-%version-%release/sys/linux
make -f LINUX/Makefile clean
rm -rf .tmp_versions/
cd ../..
cat > dkms.conf << EOF
PACKAGE_VERSION="%{version}-%{release}"

# Items below here should not have to change with each driver version
PACKAGE_NAME="%{name}"
MAKE[0]="cd sys/linux;make KERNEL_SOURCE=\${kernel_source_dir} -f LINUX/Makefile "
CLEAN="cd sys/linux;make clean -f LINUX/Makefile"
BUILT_MODULE_NAME[0]="cbm"
BUILT_MODULE_LOCATION[0]="sys/linux/"
DEST_MODULE_LOCATION[0]="/kernel/extra/"
REMAKE_INITRD="no"
AUTOINSTALL="YES"
EOF

%post -n %libname -p /sbin/ldconfig
%postun -n %libname -p /sbin/ldconfig

%post
%_install_info %name.info

%postun
%_remove_install_info %name.info

%post -n dkms-%name
dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade

%postun -n dkms-%name
dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README 
%doc docs/html docs/*.pdf
%_sysconfdir/udev/rules.d/*
%{_bindir}/*
%{_infodir}/*
%{_mandir}/man1/*

%files -n %libname
%defattr(-,root,root)
%{_libdir}/lib*.so.%{major}*

%files -n %libname-devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/lib*.a

%files -n dkms-%name
%doc README
%{_usrsrc}/%{name}-%{version}-%{release}


