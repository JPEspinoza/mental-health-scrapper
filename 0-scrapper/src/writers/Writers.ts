import fs from 'fs';
import Enumerable from 'linq';

import { Context, Writer } from '../Types';
import Logger from '../util/Logger';
import DeisResults from '../deis/DeisResults';

import DeisClient from '../deis/DeisClient';

// import writers
import Gender from './Gender';
import Age from './Age';
import Month from './Month';
import Specialist from './Specialist';
import Professional from './Professional';
import SpecialGroup from './SpecialGroup';
import EstablishmentsByCommune from './EstablishmentByCommune'; // brings the establishments in each commune, only used for generating the Constants.ts file

const logger = Logger.get('Writers');

const WRITERS: Writer[] = [
	Gender,
	Age,
	Month,
	Specialist,
	// Professional,
	// SpecialGroup
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
