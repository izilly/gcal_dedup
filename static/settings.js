function restore_check(id, current) {
  var element = document.getElementById(id);
  element['checked'] = current;
}

function restore_value(id, current) {
  var element = document.getElementById(id);
  element['value'] = current;
}

var check_settings = ['dryrun', 'created_earliest', 'updated_earliest', 'min_chars', 'ignore_attrs_num', 'ascending', 'descending'];
for (i of check_settings) {
  restore_check (i, current_settings[i]);
}

var value_settings = ['size_diff_threshold'];
for (i of value_settings) {
    restore_value (i, current_settings[i]);
}



//Object.keys(current_settings).forEach(function (k) {
  //restore_check (k, current_settings[k]);
//});

