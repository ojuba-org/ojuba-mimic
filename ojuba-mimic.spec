%global owner ojuba-org
%global commit #Write commit number here

Name:		ojuba-mimic
Obsoletes:	mimic
Summary:	Ojuba Multi Media Converter
URL:		http://ojuba.org
Version:	0.2.4
Release:	2%{?dist}
Source:		https://github.com/%{owner}/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz
License:	WAQFv2
Group:		Applications/Multimedia
BuildArch:	noarch
BuildRequires:	python2
BuildRequires:	python2-devel
BuildRequires:	ImageMagick
Requires:	python2
Requires:	ffmpeg
Requires:	pygobject3 >= 3.0.2

%description
Ojuba Multi Media Converter based on ffmpeg

%prep
%setup -q -n %{name}-%{commit}

%build
make %{?_smp_mflags}

%install
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

%files
%doc waqf2-ar.pdf
%{_bindir}/%{name}
%{python2_sitelib}/*
# %{python_sitelib}/*.egg-info
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_datadir}/applications/*.desktop
%{_datadir}/locale/*/*/*.mo

%changelog
* Sun Feb 16 2014 Mosaab Alzoubi <moceap@hotmail.com> - 0.2.4-2
- General Revision.

* Sun Jun 2 2012  Muayyad Saleh AlSadi <alsadi@ojuba.org> - 0.2.4-1
- OOP style
- new structure
- make it translatable
- port to gtk3

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
