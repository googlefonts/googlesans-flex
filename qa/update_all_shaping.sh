#!/bin/sh

for file in shaping_input/*.toml; do
    if [ -f "$file" ]; then
        python3 update_shaping_test_data.py "$file" ../fonts/variable/*.ttf
        echo "$file -> json write successful..."
    fi
done
