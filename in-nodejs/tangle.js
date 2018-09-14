#!/usr/bin/node
"use strict";

const fs = require("fs");

function tangle (input_file_name, output_file_name) {
  let line_array =
      fs.readFileSync(input_file_name)
      .toString()
      .split("\n");
  let cursor = 0;
  let result_array = [];
  while (cursor < line_array.length) {
    let line = line_array[cursor];
    cursor = 1 + cursor;
    if (line.match(/#\+property: tangle .*/)) {
    } else if (line.match(/#\+begin_src.*/)) {
      while (cursor < line_array.length) {
        let line = line_array[cursor];
        cursor = 1 + cursor;
        if (line.match(/#\+end_src.*/)) {
          break;
        }  else {
          result_array.push(line);
        }
      };
    } else {
      // do nothing
    }
  }
//   console.log("- tangle :",
//               input_file_name,
//               "->",
//               output_file_name);
  fs.writeFileSync(
    output_file_name,
    line_array_to_string(result_array));
}

function line_array_to_string (line_array) {
  let result_string = "";
  for (let line of line_array) {
    result_string = result_string.concat(line, "\n");
  }
  return result_string;
}

tangle("cicada-script.org", "cicada-script.js");
tangle("core-script.org", "core-script.cs");
