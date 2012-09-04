#
# spec file for package pywps (3.2.1)
#
# Copyright (c) 2012 Angelos Tzotsos <tzotsos@opensuse.org>
#
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           pywps
Version:        3.2.1
Release:        1
License:        GPL
Summary:        OGC Web Processing Servisce in Python
Url:            http://pywps.wald.intevation.org/index.html
Group:          Development/Tools
Source0:        %{name}-%{version}.tar.gz
BuildRequires:  fdupes
BuildRequires:  python-devel python-xml python-htmltmpl python-setuptools
Requires:       python python-xml python-htmltmpl

BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%{py_requires}

%description
Python Web Processing Service is an implementation of the Web processing Service standard from Open Geospatial Consortium.

%prep
%setup -q -n "%{name}-%{version}"

%build

%install
%__python setup.py install --prefix=%{_prefix} --root=%{buildroot} --record=FILE_LIST
%fdupes %{buildroot}%{python_sitearch}

%clean
%__rm -rf %{buildroot}

%files -f FILE_LIST
%defattr(-,root,root)
%dir %{python_sitelib}/pywps
%{python_sitelib}/pywps/

%changelog
