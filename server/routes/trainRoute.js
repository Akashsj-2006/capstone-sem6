const express = require("express");
const multer = require("multer");
const path = require("path");
const { exec } = require("child_process");

const router = express.Router();

const storage = multer.diskStorage({
 destination:"uploads/",
 filename:(req,file,cb)=>{
  cb(null,Date.now()+path.extname(file.originalname));
 }
});

const upload = multer({storage});

router.post("/",upload.single("file"),(req,res)=>{

 const filePath = req.file.path;

 exec(`python ml/train.py ${filePath}`,(error,stdout,stderr)=>{

    if(error){
        console.log(stderr)
        return res.status(500).json({error:"Training failed"})
    }

    const result = JSON.parse(stdout)

    res.json(result)

 })

})

module.exports = router;