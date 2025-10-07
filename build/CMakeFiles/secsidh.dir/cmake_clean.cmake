file(REMOVE_RECURSE
  "lib/libsecsidh.a"
  "lib/libsecsidh.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang ASM C)
  include(CMakeFiles/secsidh.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
