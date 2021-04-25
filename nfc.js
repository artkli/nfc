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

                const c = spawn('python', ['/home/pi/nfc/app/send_irc.py', 'tv']);
                c.on('close', (code) => {
                        console.log(`SEND POWER TO N command, exit code ${code}`);
                });
            }
            if (sdata.includes("REC")) {
                console.log(`${reader.reader.name}  REC string found`);

                const c = spawn('python', ['/home/pi/nfc/app/send_irc.py', 'rec']);
                c.on( 'close', ( code ) => {
                        console.log(`SEND REC TO N command, exit code ${code}`);
                });
            }
            if (sdata.includes("STOP")) {
                console.log(`${reader.reader.name}  STOP string found`);

                const c = spawn('python', ['/home/pi/nfc/app/send_irc.py', 'stop']);
                c.on('close', (code) => {
                        console.log(`SEND STOP TO N command, exit code ${code}`);
                } );
            }
            if (sdata.includes("LIST")) {
                console.log(`${reader.reader.name}  REC string found`);

                const c = spawn('python', ['/home/pi/nfc/app/send_irc.py', 'list']);
                c.on( 'close', ( code ) => {
                        console.log(`SEND REC TO N command, exit code ${code}`);
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
