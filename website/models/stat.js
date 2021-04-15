const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const statsSchema = new Schema({
    value: {
        type: Number,
        required: true
    },
    name: {
        type: String,
        required: true
    },

});

const Stat = mongoose.model('stats', statsSchema);
module.exports = Stat; 