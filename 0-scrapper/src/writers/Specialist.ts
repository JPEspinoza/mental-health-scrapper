import { Context } from '../Types';
import fs from 'fs';
import DeisResults from '../deis/DeisResults';
import DeisClient from '../deis/DeisClient';
import { COMUNAS } from '../Constants';

const PAYLOADS = [
	'ConsultationSpecialist',
];

export default class Specialist {
	public static getRequiredPayloads(): string[] {
		return PAYLOADS;
	}

	public static write(_context: Context, _client: DeisClient, results: DeisResults): void {
		for (const payload of PAYLOADS)
		{
			for (const commune of COMUNAS) {
				const comuna = commune.commune;
				for (const establishment of commune.establishments) 
				{
					// get all the data from the results
					console.log(`Writing result for ${payload}-${comuna}-${establishment}`);
					const results_array = results.get(`${payload}-${comuna}-${establishment}`)['data']['valueList'];

					let specialist_order;

					try {
						specialist_order = results.get(`${payload}-${comuna}-${establishment}`)['stringTable']['valueList'];
					}
					catch(e) {
						specialist_order = ['Psiquiatría Adulto','Psiquiatría Pediátrica y del Adolescente'];
					}

					const result_string  = JSON.stringify({
						'report': payload,
						'commune': comuna,
						'establishment': establishment,
						'columns': ['year', 'specialist', 'value'],
						'specialist_order': specialist_order,
						'data': results_array
					});

					fs.writeFile(`data/${payload}-${comuna}-${establishment}.json`, result_string, function (err: any) {
						if (err) throw err;
					});
				}
			}
		}
	}

}