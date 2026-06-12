#!/bin/zsh
# Parallel acts mirror: 4 processes, year-sliced round-robin.
cd ~/workspace/whiplash || exit 1

python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree act/public/1865 act/public/1873 act/public/1878 act/public/1887 act/public/1893 act/public/1898 act/public/1904 act/public/1908 act/public/1912 act/public/1916 act/public/1920 act/public/1924 act/public/1928 act/public/1932 act/public/1936 act/public/1940 act/public/1944 act/public/1948 act/public/1952 act/public/1956 act/public/1960 act/public/1964 act/public/1968 act/public/1972 act/public/1976 act/public/1980 act/public/1984 act/public/1988 act/public/1992 act/public/1996 act/public/2000 act/public/2004 act/public/2008 >> data-raw/mirror-p1.log 2>&1 &
P1=$!
python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree act/public/1858 act/public/1872 act/public/1876 act/public/1886 act/public/1892 act/public/1897 act/public/1903 act/public/1907 act/public/1911 act/public/1915 act/public/1919 act/public/1923 act/public/1927 act/public/1931 act/public/1935 act/public/1939 act/public/1943 act/public/1947 act/public/1951 act/public/1955 act/public/1959 act/public/1963 act/public/1967 act/public/1971 act/public/1975 act/public/1979 act/public/1983 act/public/1987 act/public/1991 act/public/1995 act/public/1999 act/public/2003 act/public/2007 >> data-raw/mirror-p2.log 2>&1 &
P2=$!
python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree act/public/1871 act/public/1875 act/public/1885 act/public/1890 act/public/1896 act/public/1902 act/public/1906 act/public/1910 act/public/1914 act/public/1918 act/public/1922 act/public/1926 act/public/1930 act/public/1934 act/public/1938 act/public/1942 act/public/1946 act/public/1950 act/public/1954 act/public/1958 act/public/1962 act/public/1966 act/public/1970 act/public/1974 act/public/1978 act/public/1982 act/public/1986 act/public/1990 act/public/1994 act/public/1998 act/public/2002 act/public/2006 >> data-raw/mirror-p3.log 2>&1 &
P3=$!
python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree act/public/1870 act/public/1874 act/public/1879 act/public/1888 act/public/1895 act/public/1901 act/public/1905 act/public/1909 act/public/1913 act/public/1917 act/public/1921 act/public/1925 act/public/1929 act/public/1933 act/public/1937 act/public/1941 act/public/1945 act/public/1949 act/public/1953 act/public/1957 act/public/1961 act/public/1965 act/public/1969 act/public/1973 act/public/1977 act/public/1981 act/public/1985 act/public/1989 act/public/1993 act/public/1997 act/public/2001 act/public/2005 >> data-raw/mirror-p4.log 2>&1 &
P4=$!

wait $P1 $P2 $P3 $P4
echo "=== ACTS DONE, starting regulations ===" >> data-raw/mirror.log
python3 pipeline/mirror.py data-raw/legislation --gap 0.2 --workers 4 --subtree regulation/public >> data-raw/mirror.log 2>&1
echo "=== ALL MIRROR DONE ===" >> data-raw/mirror.log
