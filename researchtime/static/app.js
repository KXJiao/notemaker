$(document).ready(function() { 

    ////////////////////////////////Stuff for TinyMCE editable textbox////////////////

    $('#textinput').tinymce({
        script_url: 'static/tinymce.min.js',
        toolbar: false,
        menubar:false,
        statusbar:false,
        plugins: 'autoresize paste',
        paste_as_text: true
    });
    $('#textsummary').tinymce({
        script_url: 'static/tinymce.min.js',
        plugins: 'autoresize lists',
        resize: false 
    });
    $('#highlighttext').tinymce({
        script_url: 'static/tinymce.min.js',
        toolbar: false,
        menubar:false,
        statusbar:false,
        plugins: 'autoresize'
    });

    /////////////////////////////////////////////////////////////////////////////////

    function highlight(e){
        alert('hello')
    }

    $('#fileupload').hide();
    $('#textbox').hide();
    $('#externalurl').hide();
    $('#hidethis').show();
    $('#htl').hide();
    $('#tsr').hide();
    $('#loading').hide();
    $('#errors').text('')
    $('#tsubject').text('')


    $('#gotoupload').click(function(e){
        $('#errors').text('')
        $('#textbox').fadeOut(function(){
            $('#fileupload').fadeIn('slow');
        });
        $('#externalurl').fadeOut(function(){
            $('#fileupload').fadeIn('slow');
        });
        
    });
    $('#gototext').click(function(e){
        $('#errors').text('')
        $('#fileupload').fadeOut(function(){
            $('#textbox').fadeIn('slow');
        });
        $('#externalurl').fadeOut(function(){
            $('#textbox').fadeIn('slow');
        });
    });
    $('#gotourl').click(function(e){
        $('#errors').text('')
        $('#fileupload').fadeOut(function(){
            $('#externalurl').fadeIn('slow');
        });
        $('#textbox').fadeOut(function(){
            $('#externalurl').fadeIn('slow');
        });
    });

    // $('#textsummary').on('click', '.summarypoint', function(){
    //     spText = $(this).text();
    //     console.log(spText);

    // });
    var highlightPoints = [];
    tinymce.get('textsummary').on('click', function(e){
        if ($(e.target).attr('class') == 'summarypoint'){
            spTextIndex = $(e.target).attr('highlightid');
            spText = highlightPoints[parseInt(spTextIndex)];
            hlText = tinyMCE.get('highlighttext').getContent({ format: 'text' });
            hlText = hlText.replace(spText, '<mark>' + spText + '</mark>');
            tinyMCE.get('highlighttext').setContent(hlText);
            // hlIndex = hlText.indexOf(spText)
            // hlEndex = -1
            // if (!(hlIndex == -1)){
            //     hlEndex = hlIndex + spText.length;
            // }
            // console.log("index: " + hlIndex + " endex: " + hlEndex)
        }
    });


    var files;
    $('#file').on('change', function(event) { 
        $('#errors').text('')
        files = event.target.files;
    }); 
/////////////////////File uploader

    
    $('#fileupload').on('submit', function(event){
        //event.stopPropagation();
        event.preventDefault();
        $('#errors').text('')
        $('#upload').prop('disabled',true);
        $('#compare').prop('disabled',true);
        $('#external').prop('disabled',true);

        if($('#file')[0].files[0].size < 5242880){
            $('#loading').show();
            var sentNum = $('#sentNum').val();
            if(!sentNum || isNaN(sentNum)){
                sentNum = '5';
            }
            var data = new FormData();
            data.append('sentNum', sentNum);
            data.append('file', $('#file')[0].files[0]);

            $.ajax({
                url: '/fileupload',
                type: 'POST',
                contentType: false,
                processData: false,
                dataType: 'json',
                data: data,         
                success: function(data){
                    $('#loading').hide();
                    $('#htl').show();
                    $('#tsr').show();
                    $('#tsubject').text(data.subject)
                    $('#hidethis').hide();
                    $('#upload').prop('disabled',false);
                    $('#compare').prop('disabled',false);
                    $('#external').prop('disabled',false);
                    tinymce.get('highlighttext').setContent(data.og);
                    var addText = '<ul>'
                    for(i = 0; i<data.summary.length; i++){
                        addText = addText + '\n' + '<li class="summarypoint" highlightid = "' + highlightPoints.length + '"">' + data.summary[i] + '</li>'
                        highlightPoints.push(data.summary[i]);
                    }
                    addText = addText + '</ul>'
                    $('#textsummary_ifr').contents().find('#tinymce').append(addText);

                    $('html, body').animate({
                        scrollTop: $('#portfolio').offset().top
                    }, 500);

                    tinymce.execCommand('mceFocus',false,'textsummary');
                },
                error: function(data){
                    $('#upload').prop('disabled',false);
                    $('#compare').prop('disabled',false);
                    $('#external').prop('disabled',false);
                    $('#loading').hide();
                    $('#errors').text('There was an error. Maybe the file has too many words?')
                }
            })
        }
        else{
            $('#errors').text('File should be < 5MB')
        }

    });


///////////////////////////Textbox
    var request;
    $('#textbox').on('submit', function(event){
        event.preventDefault();
        $('#upload').prop('disabled',true);
        $('#compare').prop('disabled',true);
        $('#external').prop('disabled',true);
        $('#errors').text('')
        $('#loading').show();
        var sentNum = $('#sentNum').val()
        var text = $('#textinput').val()

        $.ajax({
            url: '/summarize',
            type: 'post',
            contentType: 'application/json; charset=utf8',
            dataType: 'json',
            data: JSON.stringify({
                type: 'text',
                num: sentNum,
                data: text
            }),
            success: function(data){
                $('#loading').hide();
                $('#htl').show();
                $('#tsr').show();
                //data.og = original text, data.summary = array of summary points
                $('#tsubject').text(data.subject)
                $('#hidethis').hide();
                $('#upload').prop('disabled',false);
                $('#compare').prop('disabled',false);
                $('#external').prop('disabled',false);
                tinymce.get('highlighttext').setContent(data.og);

                //handle text highlighting here: when clicking the summary point, will highlight in original text

                var addText = '<ul>'
                for(i = 0; i<data.summary.length; i++){
                    addText = addText + '\n' + '<li class="summarypoint" highlightid = "' + highlightPoints.length + '"">' + data.summary[i] + '</li>'
                    highlightPoints.push(data.summary[i]);
                }
                addText = addText + '</ul>'
                $('#textsummary_ifr').contents().find('#tinymce').append(addText);
                
                $('html, body').animate({
                    scrollTop: $('#portfolio').offset().top
                }, 500);

                tinymce.execCommand('mceFocus',false,'textsummary');
               
                
            },
            error: function(error){
                $('#upload').prop('disabled',false);
                $('#compare').prop('disabled',false);
                $('#external').prop('disabled',false);
                $('#loading').hide();
                $('#errors').text('There was an error. Maybe there are too many words?')
            }
        });
    });


    /////////////////////////URL
    $('#externalurl').on('submit', function(e){
        e.preventDefault();
        $('#upload').prop('disabled',true);
        $('#compare').prop('disabled',true);
        $('#external').prop('disabled',true);
        $('#errors').text('')
        $('#loading').show();
        var sentNum = $('#sentNum').val();
        var url = $('#url').val();
        //verify the url 

        $.ajax({
            url: '/summarize',
            type: 'post',
            contentType: 'application/json; charset=utf8',
            dataType: 'json',
            data: JSON.stringify({
                type: 'url',
                num: sentNum,
                data: url
            }),
            success: function(data){
                $('#loading').hide();
                $('#htl').show();
                $('#tsr').show();
                //data.og = original text, data.summary = array of summary points
                $('#tsubject').text(data.subject)
                $('#hidethis').hide();
                $('#upload').prop('disabled',false);
                $('#compare').prop('disabled',false);
                $('#external').prop('disabled',false);
                tinymce.get('highlighttext').setContent(data.og);

                //handle text highlighting here: when clicking the summary point, will highlight in original text

                var addText = '<ul>'
                for(i = 0; i<data.summary.length; i++){
                    addText = addText + '\n' + '<li class="summarypoint" highlightid = "' + highlightPoints.length + '"">' + data.summary[i] + '</li>'
                    highlightPoints.push(data.summary[i]);
                }
                addText = addText + '</ul>'
                $('#textsummary_ifr').contents().find('#tinymce').append(addText);
                
                $('html, body').animate({
                    scrollTop: $('#portfolio').offset().top
                }, 500);

                tinymce.execCommand('mceFocus',false,'textsummary');
            },
            error: function(data){
                $('#upload').prop('disabled',false);
                $('#compare').prop('disabled',false);
                $('#external').prop('disabled',false);
                $('#loading').hide();
                $('#errors').text('There was an error. Maybe the file has too many words?')
            }
        });


    });
    
}); 
