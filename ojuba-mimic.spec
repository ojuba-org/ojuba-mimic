Name: ojuba-mimic
Obsoletes: mimic
Summary: Ojuba Multi Media Converter based on ffmpeg
URL: http://www.ojuba.org
Version: 0.1.6
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.bz2
License: Waqf
Group: Applications/Multimedia
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python
Requires: python, pygtk2, ffmpeg

# %{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%description
Ojuba Multi Media Converter based on ffmpeg

%prep
%setup -q -n %{name}
%build

%install
rm -rf $RPM_BUILD_ROOT

install -d -p -m 755 $RPM_BUILD_ROOT%{_bindir}
install -d -p -m 755 $RPM_BUILD_ROOT%{_datadir}/applications
install -D -p -m 755 %{name}.py $RPM_BUILD_ROOT%{_bindir}/%{name}
desktop-file-install \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  %{name}.desktop
#mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/32x32/apps
#install -p -m 644 %{SOURCE1} \
#  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/32x32/apps

%clean
rm -rf $RPM_BUILD_ROOT

%files
%doc LICENSE-en LICENSE-ar.txt
%{_bindir}/%{name}
%{_datadir}/applications/*
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

