const express = require('express');
const morgan = require('morgan');
const mongoose = require('mongoose');
const Stat = require('./models/stat');
const dotenv = require('dotenv').config({path:'../.env'});

//express app
const app = express();

//connect to mongodb
const dbURI = process.env.DATABASE_URL;
mongoose.connect(dbURI, { useNewUrlParser: true, useUnifiedTopology: true } )
    .then((result)=> app.listen(3000))
    .catch((err) => console.log(err));

app.set('view engine', 'ejs');

app.use(express.static('public'));
app.use(morgan('dev'));

//register view engine
app.set('view engine', 'ejs');

//logging
app.use((req,res, next) => {
    console.log('new request made: ');
    console.log('host: ', req.hostname);
    console.log('path: ', req.path);
    console.log('method: ', req.method);
    next();
});

//mongo routes
app.get('/index', (req,res) => {
    Stat.find()
    .then((result) => {
        console.log(result);
        res.render('index', {stats: result})
    })
    .catch((err) => {
        console.log(err);
    })
});

app.get('/', (req,res) =>{

    res.redirect('index');
});

app.use((req,res, next) => {
    console.log('in the next middleware');
    next();
});

app.get('/about', (req,res) =>{

    res.render('about');
});

app.get('/commands', (req, res) => {
    res.render('commands');
});

app.get('/documentation', (req, res) => {
    res.render('documentation');
});

app.get('/doc', (req, res) => {
    res.redirect('documentation');
});



// 404 page
app.use((req,res) => {
    res.status(404).sendFile('./views/404.html', {root: __dirname});
});