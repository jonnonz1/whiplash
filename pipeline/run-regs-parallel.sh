#!/bin/zsh
cd ~/workspace/whiplash || exit 1

python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree regulation/public/1938 regulation/public/1942 regulation/public/1946 regulation/public/1950 regulation/public/1954 regulation/public/1958 regulation/public/1962 regulation/public/1966 regulation/public/1970 regulation/public/1974 regulation/public/1978 regulation/public/1982 regulation/public/1986 regulation/public/1990 regulation/public/1994 regulation/public/1998 regulation/public/2002 regulation/public/2006 regulation/public/2010 regulation/public/2014 regulation/public/2018 >> data-raw/mirror-r1.log 2>&1 &
R1=$!
python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree regulation/public/1937 regulation/public/1941 regulation/public/1945 regulation/public/1949 regulation/public/1953 regulation/public/1957 regulation/public/1961 regulation/public/1965 regulation/public/1969 regulation/public/1973 regulation/public/1977 regulation/public/1981 regulation/public/1985 regulation/public/1989 regulation/public/1993 regulation/public/1997 regulation/public/2001 regulation/public/2005 regulation/public/2009 regulation/public/2013 regulation/public/2017 >> data-raw/mirror-r2.log 2>&1 &
R2=$!
python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree regulation/public/1936 regulation/public/1940 regulation/public/1944 regulation/public/1948 regulation/public/1952 regulation/public/1956 regulation/public/1960 regulation/public/1964 regulation/public/1968 regulation/public/1972 regulation/public/1976 regulation/public/1980 regulation/public/1984 regulation/public/1988 regulation/public/1992 regulation/public/1996 regulation/public/2000 regulation/public/2004 regulation/public/2008 regulation/public/2012 regulation/public/2016 >> data-raw/mirror-r3.log 2>&1 &
R3=$!
python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree regulation/public/1887 regulation/public/1939 regulation/public/1943 regulation/public/1947 regulation/public/1951 regulation/public/1955 regulation/public/1959 regulation/public/1963 regulation/public/1967 regulation/public/1971 regulation/public/1975 regulation/public/1979 regulation/public/1983 regulation/public/1987 regulation/public/1991 regulation/public/1995 regulation/public/1999 regulation/public/2003 regulation/public/2007 regulation/public/2011 regulation/public/2015 >> data-raw/mirror-r4.log 2>&1 &
R4=$!
python3 pipeline/mirror.py data-raw/legislation --gap 0.25 --subtree regulation/public/2019 regulation/public/2020 regulation/public/2021 regulation/public/2022 regulation/public/2023 regulation/public/2024 regulation/public/2025 regulation/public/2026 >> data-raw/mirror-r5.log 2>&1 &
R5=$!

wait $R1 $R2 $R3 $R4 $R5
echo "=== ALL MIRROR DONE ===" >> data-raw/mirror.log
