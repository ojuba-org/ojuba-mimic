%global owner ojuba-org

Name: ojuba-mimic
Summary: MultiMedia Converter
Summary(ar): محوّل وسائط
URL: http://ojuba.org
Version: 0.3
Release: 1%{?dist}
Source: https://github.com/%{owner}/%{name}/archive/%{version}/%{name}-%{version}.tar.gz
License: WAQFv2
BuildArch: noarch
BuildRequires: intltool
BuildRequires: python2-devel
BuildRequires: ImageMagick
Requires: python2
Requires: ffmpeg
Requires: pygobject3 >= 3.0.2

%description
Ojuba Multi Media Converter based on ffmpeg

%description -l ar
محوّل وسائط أعجوبة متوافق مع محرّك ffmpeg

%prep
%autosetup -n %{name}-%{version}

%build
make %{?_smp_mflags}

%install
%make_install



# Register as an application to be visible in the software center
#
# NOTE: It would be *awesome* if this file was maintained by the upstream
# project, translated and installed into the right place during `make install`.
#
# See http://www.freedesktop.org/software/appstream/docs/ for more details.
#
mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata
cat > $RPM_BUILD_ROOT%{_datadir}/appdata/%{name}.appdata.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2017 Mosaab Alzoubi <moceap@hotmail.com> -->
<!--
EmailAddress: moceap@hotmail.com
SentUpstream: 2017-1-8
-->
<application>
  <id type="desktop">ojuba-mimic.desktop</id>
  <metadata_license>CC0-1.0</metadata_license>
  <summary>Multimedia Convertor</summary>
  <summary xml:lang="ar">محول وسائط</summary>
  <description>
    <p>
	Ojuba Multi Media Converter based on ffmpeg.
    </p>
  </description>
  <description xml:lang="ar">
    <p>
	محوّل وسائط أعجوبة متوافق مع محرّك ffmpeg.
    </p>
  </description>
  <url type="homepage">https://github.com/ojuba-org/%{name}</url>
  <screenshots>
    <screenshot type="default">http://ojuba.org/screenshots/%{name}.png</screenshot>
  </screenshots>
  <updatecontact>moceap@hotmail.com</updatecontact>
</application>
EOF




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
%license waqf2-ar.pdf
%{_bindir}/%{name}
%{python2_sitelib}/*
# %{python_sitelib}/*.egg-info
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_datadir}/applications/*.desktop
%{_datadir}/locale/*/*/*.mo
%{_datadir}/appdata/%{name}.appdata.xml

%changelog
* Mon Jan 9 2017 Mosaab Alzoubi <moceap@hotmail.com> - 0.3-1
- Update to 0.3
- New way to Github
- Add Appdata

* Wed Jul 22 2015 Mosaab Alzoubi <moceap@hotmail.com> - 0.2.4-3
- Remove old obsolete
- Improve Summary
- Add Arabic Summary and Description
- Remove Group tag
- Update BRs
- Use %%make_install
- Use %%license

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
