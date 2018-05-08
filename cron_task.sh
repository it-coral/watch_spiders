#!/bin/bash
0 7 * * 1 sh -c " if [ $(expr $(expr $(date +\%s) \/ 604800) \% 2) -eq 0 ]; then command; fi " scrapy crawl cresuswatches
0 7 * * 1 sh -c " if [ $(expr $(expr $(date +\%s) \/ 604800) \% 2) -eq 0 ]; then command; fi " scrapy crawl filipucci
0 7 * * 1 sh -c " if [ $(expr $(expr $(date +\%s) \/ 604800) \% 2) -eq 0 ]; then command; fi " scrapy crawl lieblingskapital