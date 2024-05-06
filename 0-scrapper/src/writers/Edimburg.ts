import { Context } from '../Types';
import fs from 'fs';
import DeisResults from '../deis/DeisResults';
import DeisClient from '../deis/DeisClient';
import { COMUNAS } from '../Constants';

const PAYLOADS = [
	'EdimburgPostPartum',
	'EdimburgPregnant',
	'MCHAT18month',
	'MCHAT30month',

	// month
	'ConsultationSpecialistByMonth',
	'AttendanceByMonth',
	'ConsultationByMonth',

	// age
	'AttendanceByAge',
	'ConsultationByAge',
	'ConsultationSpecialistByAge',

	// gender
	'AttendanceByGender',
	'ConsultationByGender',
	'ConsultationSpecialistByGender',

	// specialist
	'ConsultationSpecialist',

	// professional
	'AttendanceByProfessional',

	// special group
	'ConsultationBySpecialGroup'

];

export default class Edimburg {
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

					const result = results.get(`${payload}-${comuna}-${establishment}`);

					// if no valueList, skip
					if (!result['data']['valueList']) {
						continue;
					}
					const data = result['data']['valueList'];

					// get columns
					// result['variables']
					const columns = [];
					const variables = result['variables'];
					for (let i = 0; i < variables.length; i++) {
						columns.push(variables[i]['label']);
					}

					// get stringtable
					let stringTable = null;
					try {
						stringTable = result['stringTable']['valueList'];
					}
					catch(e) {
						stringTable = null;
					}

					const result_string  = JSON.stringify({
						'report': payload,
						'commune': comuna,
						'establishment': establishment,
						'stringTable': stringTable, 
						'columns': columns,
						'data': data,
					});

					fs.writeFile(`data/${payload}-${comuna}-${establishment}.json`, result_string, function (err: any) {
						if (err) throw err;
					});
				}
			}
		}
	}
}