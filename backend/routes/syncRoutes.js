const express = require('express');
const router = express.Router();
const PouchDB = require('pouchdb');
const ExpressPouchDB = require('express-pouchdb');

// Configurer le middleware express-pouchdb pour gérer les requêtes PouchDB
const pouchDBServer = ExpressPouchDB(PouchDB);

// Route pour la synchronisation PouchDB
router.use('/', pouchDBServer);

module.exports = router; 