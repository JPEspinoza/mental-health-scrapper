/*

This writer scraps the list of establishments by commune and writes it to a JSON file.

*/

import { Context } from '../Types';
import fs from 'fs';
import DeisResults from '../deis/DeisResults';
import DeisClient from '../deis/DeisClient';
import { COMUNAS } from '../Constants';

const PAYLOADS = [
	'EstablishmentsByCommune',
];

const COLUMNS = ['establishment'];

export default class EstablishmentsByCommune {
	public static getRequiredPayloads(): string[] {
		return PAYLOADS;
	}

	public static write(_context: Context, _client: DeisClient, results: DeisResults): void {
		for (const payload of PAYLOADS) {
			for (const commune of COMUNAS) {
				const comuna = commune.commune;
				// get all the data from the results
				console.log(`Writing result for ${payload}-${comuna}`);
				let results_array;
				try {
					results_array = results.get(`${payload}-${comuna}`)['stringTable']['valueList'];
				}
				catch (e) {
					results_array = results.get(`${payload}-${comuna}`)['data']['valueList'][0];
				}

				const result_string = JSON.stringify({
					'report': payload,
					'commune': comuna,
					'columns': COLUMNS,
					'data': results_array
				});

				fs.writeFile('data/' + payload + '-' + comuna + '.json', result_string, function (err: any) {
					if (err) throw err;
				});
			}
		}
	}
}