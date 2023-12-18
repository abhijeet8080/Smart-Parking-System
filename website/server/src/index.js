const express = require("express");
const path = require("path");
const bcrypt = require("bcrypt");
const collection = require("./config");
const cors = require("cors");
const app = express();
app.use(express.json());
app.use(express.urlencoded({extended:true}));
app.use(cors());
app.post("/signup",async(req,res)=>{
    
    const data= {
        name : req.body.name,
        email : req.body.email,
        password : req.body.password
    }
    console.log(data.name)
    console.log(data.email)
    console.log(data.password)
    const existingUser = await collection.findOne({email:data.email});
    if(existingUser){
        console.log("User already exists");
        res.json("exist");
    }
    else{
        const saltRounds = 10;
        const hashedPassword = await bcrypt.hash(data.password,saltRounds);
        data.password = hashedPassword;
        const userData = await collection.insertMany(data);
        console.log(userData);
        res.json("not exist");
    }
})
app.post("/login", async(req,res)=>{
    console.log("Request has been made");
    email = req.body.email;
    console.log(email);
try{
    const check = await collection.findOne({email:email})
        if(check){
            const isPasswordMatch = await bcrypt.compare(req.body.password,check.password);
            if(isPasswordMatch){
                res.json("exist");
                console.log("Password matched");
            }
            else{
                res.json("wrong password");
                console.log("Wrong Password")
            }
        }
        else{
            res.json("not exist");
            
        }
}
catch{
    console.log("Wrong Details");
}
})
const port = 5000;
app.listen(5000,()=>{
    console.log("Server is running 5000");
})