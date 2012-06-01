Name: ojuba-mimic
Obsoletes: mimic
Summary: Ojuba Multi Media Converter based on ffmpeg
URL: http://www.ojuba.org
Version: 0.2.3
Release: 1%{?dist}
Source0: http://git.ojuba.org/cgit/%{name}/snapshot/%{name}-%{version}.tar.bz2
License: Waqf
Group: Applications/Multimedia
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python, ImageMagick
Requires: python, ffmpeg
Requires:   pygobject3 >= 3.0.2
# %{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%description
Ojuba Multi Media Converter based on ffmpeg

%prep
%setup -q

%build
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall DESTDIR=$RPM_BUILD_ROOT

%post
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ] ; then
%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%postun
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ] ; then
%{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%doc LICENSE-en LICENSE-ar.txt
%{_bindir}/%{name}
%{python_sitelib}/*
# %{python_sitelib}/*.egg-info
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_datadir}/applications/*.desktop
%{_datadir}/locale/*/*/*.mo

%changelog
* Sun Jun 6 2010  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.6-1
- update to recent ffmpeg (one with libopencore_amrnb) 

* Sat Jan 31 2009  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.4-1
- include a copy of the license

* Mon Dec 22 2008  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.3-1
- skip protocol for DND files

* Sat Dec 20 2008  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.2-1
- Give the verse a background color (look nicer in dark themes)

* Fri Dec 19 2008  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.1-1
- Drag and Drop support

* Sun Aug 03 2008  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.1.0-1
- Initial packing

