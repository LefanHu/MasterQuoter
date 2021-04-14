const express = require('express');
const morgan = require('morgan');

//express app
const app = express();

app.set('view engine', 'ejs');

//listen for requests
app.listen(3000);

app.use(express.static('public'));
app.use(morgan('dev'));


//logging
app.use((req,res, next) => {
    console.log('new request made: ');
    console.log('host: ', req.hostname);
    console.log('path: ', req.path);
    console.log('method: ', req.method);
    next();
});




app.get('/', (req,res) =>{

    res.render('index', {title:'Home'});
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



// 404 page
app.use((req,res) => {
    res.status(404).sendFile('./views/404.html', {root: __dirname});
})