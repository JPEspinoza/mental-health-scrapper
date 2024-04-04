import fs from 'fs';
import Enumerable from 'linq';

import { Context, Writer } from '../Types';
import Logger from '../util/Logger';
import DeisResults from '../deis/DeisResults';

import DeisClient from '../deis/DeisClient';
import MentalByGender from './MentalByGender';
import MentalByAge from './MentalByAge';
import MentalByMonth from './MentalByMonth';
import MentalByProfessional from './MentalByProfessional';
import EstablishmentsByCommune from './EstablishmentByCommune';

const logger = Logger.get('Writers');

const WRITERS: Writer[] = [
	MentalByGender,
	MentalByAge,
	MentalByMonth,
	MentalByProfessional,
	// EstablishmentsByCommune // brings the establishments in each commune, only used for generating the Constants.ts file
];

export default class Writers
{
	public static getRequiredPayloads(): string[] {
		return Enumerable
			.from(WRITERS)
			.where(w => !w.isEnabled || w.isEnabled())
			.selectMany(w => w.getRequiredPayloads())
			.distinct()
			.orderBy(p => p)
			.toArray();
	}

	public static async write(context: Context, client: DeisClient, results: DeisResults): Promise<void>
	{
		// create data/ folder if not exists
		if (!fs.existsSync('data/'))
		{
			fs.mkdirSync('data/');
		}

		for (const writer of WRITERS)
		{
			if (writer.isEnabled && !writer.isEnabled())
			{
				logger.info(`Skipping: ${writer.name}...`);
				continue;
			}

			logger.info(`Writing ${writer.name}...`);
			await Promise.resolve(writer.write(context, client, results));
		}
	}
}
