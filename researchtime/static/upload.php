<?php
$data = array();
if(isset($_GET['files'])){
    $error = false;
    $files = array();
    
    switch(strtolower($_FILES['files']['type'])){
            //allowed file types
            case 'image/png': 
            case 'image/jpeg': 
            case 'image/pjpeg':
            case 'application/pdf':
            case 'application/msword':
            case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            case 'text/plain':
            case 'text/html':
            case 'application/epub+zip':
                break;
            default:
                die('Unsupported File!'); //output error
    }

    $File_Name          = strtolower($_FILES['files']['name']);
    $File_Ext           = substr($File_Name, strrpos($File_Name, '.')); //get file extention
    $Random_Number      = rand(0, 9999999999); //Random number to be added to name.
    $NewFileName        = $Random_Number.$File_Ext; //new file name

    $uploaddir = '../../tmp/';

    foreach($_FILES as $file){
      //if(move_uploaded_file($_FILES['file']['tmp_name'], $UploadDirectory.$NewFileName ))
        if(move_uploaded_file($file['tmp_name', $uploaddir .$NewFileName )){
            $files[] = $uploaddir .$NewFileName;
        }
        else{
            $error = true;
        }
    }
    $data = ($error) ? array('error' => 'error') : array('files' => $files);
    
}
else{
    $data = array('success' => 'submitted', 'formData' => $_POST);
}

echo json_encode($data);

?>