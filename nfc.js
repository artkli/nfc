"use strict";

import { NFC, TAG_ISO_14443_3, TAG_ISO_14443_4, KEY_TYPE_A, KEY_TYPE_B } from '../src/index';


const nfc = new NFC();

nfc.on('reader', async reader => {
    console.log(`${reader.reader.name}  device attached`);

    reader.on('card', async card => {
        if (card.type !== TAG_ISO_14443_3) {
            return;
        }

        const key = 'FFFFFFFFFFFF';
        const keyType = KEY_TYPE_B;

        try {
            await reader.authenticate(4, keyType, key);

            console.log(`${reader.reader.name}  card authenticated`);

        } catch (err) {
            console.log(`${reader.reader.name}  an error occurred`, err);
            return;
        }

        try {
            const data = await reader.read(4, 16, 16);

            const convert = (from, to) => str => Buffer.from(str, from).toString(to);
            const hexToUtf8 = convert('hex', 'utf8');

            const sdata = hexToUtf8(data);
            const removeNonASCII = str => str.replace(/[^\x20-\x7E]/g, "_");
            
            console.log(`${reader.reader.name}  data read: `, removeNonASCII(sdata));

            const {spawn} = require('child_process');
                       
            if (sdata.includes("POWER")) {
                console.log(`${reader.reader.name}  POWER string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'sat']);
                c.on('close', (code) => {
                        console.log(`SEND TV command, exit code ${code}`);
                });
            }
            if (sdata.includes("PC")) {
                console.log(`${reader.reader.name}  PC string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'pc']);
                c.on('close', (code) => {
                        console.log(`SEND TV command, exit code ${code}`);
                });
            }
            if (sdata.includes("TV")) {
                console.log(`${reader.reader.name}  TV string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'sat']);
                c.on('close', (code) => {
                        console.log(`SEND TV command, exit code ${code}`);
                });
            }
            if (sdata.includes("FILM")) {
                console.log(`${reader.reader.name}  FILM string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'film']);
                c.on('close', (code) => {
                        console.log(`SEND FILM command, exit code ${code}`);
                });
            }
            if (sdata.includes("RADIO")) {
                console.log(`${reader.reader.name}  RADIO string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'radio']);
                c.on('close', (code) => {
                        console.log(`SEND RADIO command, exit code ${code}`);
                });
            }
            if (sdata.includes("CD")) {
                console.log(`${reader.reader.name}  CD string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'cd']);
                c.on('close', (code) => {
                        console.log(`SEND CD command, exit code ${code}`);
                });
            }
            if (sdata.includes("NET")) {
                console.log(`${reader.reader.name}  NET string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'net']);
                c.on('close', (code) => {
                        console.log(`SEND NET command, exit code ${code}`);
                });
            }
            if (sdata.includes("CANAL")) {
                console.log(`${reader.reader.name}  NET string found`);

                const c = spawn('sudo', ['python3', '/home/pi/nfc/app/nfc.py', 'canal']);
                c.on('close', (code) => {
                        console.log(`SEND CANAL command, exit code ${code}`);
                });
            }
        } catch (err) {
            console.log(`${reader.reader.name}  an error occurred`, err);
        }

    });

    reader.on('error', err => {
        console.log(`${reader.reader.name}  an error occurred`, err);
    });

    reader.on('end', () => {
        console.log(`${reader.reader.name}  device removed`);
    });

});

nfc.on('error', err => {
    console.log(`an error occurred`, err);
});
