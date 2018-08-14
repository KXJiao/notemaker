<!-- <?php
    if(isset($_FILES["file"])){
        $UploadDirectory = 'tmp/';
    
        $errors= array();
        $file_name = $_FILES['file']['name'];
        $file_size =$_FILES['file']['size'];
        $file_tmp =$_FILES['file']['tmp_name'];
        $file_type=$_FILES['file']['type'];
        $file_ext=strtolower(end(explode('.',$_FILES['image']['name'])));

        $extensions =  array("doc", "docx", "pdf", "txt", "html", "htm", "epub", "jpg", "jpeg", "png");

        if(in_array($file_ext,$extensions)=== false){
            $errors[]="extension not allowed";
        }

        if(empty($errors)==true){
            move_uploaded_file($file_tmp,"images/".$file_name);
            $output = array("success" => true, "message" => "Success!");

        }else{
            print_r($errors);
            $output = array("success" => false, "error" => $errors);
        }

        if ($success) {
            $output = array("success" => true, "message" => "Success!");
        } else {
            $output = array("success" => false, "error" => "Failure!");
        }
    }

    header("Content-Type: application/json; charset=utf-8");
    echo json_encode($output);

?>

 -->