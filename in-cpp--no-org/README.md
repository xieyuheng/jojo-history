# About quit using org-mode

This `src/` tree contains an effort to quit using org-mode,
by separating one `.org` file to many `.hpp` and `.cpp` files.

I wanted to quit using org-mode,
because it will make the project more accessible to non org-mode users.

The experience are :
- The overall build time went from 10s to 130s.
- It become header to change the code :
  - changing naming in one file,
    becomes changing naming in many files and changing file name.
  - re-structuring the code in org-mode headline tree,
    becomes re-structuring the source-tree in file system.

Thus, I decide to not quit org-mode,
to make the code easier to change,
easier to re-structuring
and easier to view.
