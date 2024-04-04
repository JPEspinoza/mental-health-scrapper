
import * as fs from 'fs';
import * as path from 'path';

import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

import { DeisCredentials, DeisResult } from '../Types';
import DeisAuthScraper from './DeisAuthScraper';
import Logger from '../util/Logger';
import DeisResults from './DeisResults';
import { COMUNAS } from '../Constants';

const logger = Logger.get('DeisClient');

const BASE_URL = 'https://informesdeis.minsal.cl/reportData/jobs?indexStrings=true&embeddedData=true&wait=30';

export default class DeisClient
{
	private credentials: DeisCredentials | null = null;
	private credentialsPromise = DeisAuthScraper.getCredentials();
	private sequence = 1;

	public async queryAll(payloads: string[]): Promise<DeisResults>
	{
		logger.info('Initializing DEIS client...');
		await this.init();
		const results = new Map<string, DeisResult>();

		logger.info(`Looking though ${payloads.length} payloads...`);
		for (const payloadName of payloads)
		{
			const filePath = path.join(__dirname, '../../payloads/', `${payloadName}.json`);
			const file = fs.readFileSync(filePath).toString();	

			for (const commune of COMUNAS)
			{
				const comuna = commune.commune;
				const payload = file.replace('{0}', comuna);

				// check if payload has establishments
				// if not, skip establishments loop
				if (file.includes('{1}') === true)
				{
					console.log('Querying with establishments!');
					for (const establishment of commune.establishments)
					{
						console.log(`Querying for ${payloadName}-${comuna}-${establishment}`);
						const payload2 = payload.replace('{1}', establishment);

						const result = await this.query(payload2);
						results.set(`${payloadName}-${comuna}-${establishment}`, result);
					}
				}
				else {
					console.log(`Querying for ${payloadName}-${comuna}`);
					const result = await this.query(payload);
					results.set(`${payloadName}-${comuna}`, result);
				}
			}
		}

		return new DeisResults(results);
	}

	public async queryPayload(payload: string): Promise<DeisResult>
	{
		await this.init();
		const url = this.getUrl();
		const result = await axios({
			method: 'post',
			url: url,
			data: payload,
			headers: {
				'x-csrf-token': this.credentials?.xCsrfToken,
				'cookie': `JSESSIONID=${this.credentials?.jSessionID}`,
				'content-type': 'application/vnd.sas.report.query+json'
			},
		});
		const content = JSON.parse(result.data.results.content);

		return content.results[0] as DeisResult;
	}

	private async query(payload: string): Promise<DeisResult>
	{
		const result = await this.queryPayload(payload);
		return result;
	}

	private async init(): Promise<void>
	{
		if (this.credentials)
			return;

		logger.info('Waiting for credentials promise to resolve...');
		try
		{
			this.credentials = await this.credentialsPromise;
		}
		catch (e)
		{
			logger.error('Error while waiting for credentials: ' + e);
			throw e;
		}
	}

	private getUrl(): string
	{
		const seq = this.sequence++;
		const jobId = uuidv4();
		return BASE_URL +
			`&executorId=${this.credentials?.executorID}` +
			`&jobId=${jobId}` +
			`&sequence=${seq}`;
	}

}
