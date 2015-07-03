function enable_text_replacement() {
    var text_ids = ['rep1f', 'rep1r',
                    'rep2f', 'rep2r',
                    'rep3f', 'rep3r',
                    'rep4f', 'rep4r',
                    'rep5f', 'rep5r',
                    ];
    var alength = text_ids.length;
    
    for (var i = 0; i < alength; i++) {
         var ele = document.getElementById(text_ids[i]);
         ele.disabled = !ele.disabled;
    }
}
