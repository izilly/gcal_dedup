function restore_check(id, current) {
  var element = document.getElementById(id);
  element['checked'] = current;
}

var settings = ['dryrun', 'created_earliest', 'updated_earliest', 'min_chars'];
for (i of settings) {
  restore_check (i, current_settings[i]);
};

//Object.keys(current_settings).forEach(function (k) {
  //restore_check (k, current_settings[k]);
//});

