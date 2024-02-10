import { Box } from "@chakra-ui/react";
import { useEffect, useState } from "react";

interface ResultsPage {
	sku_id: number;
	old_location: string;
	new_location: string;
}

const ResultsPage: React.FC = () => {
	const [skusWithLocations, setSkusWithLocations] = useState<ResultsPage[]>([]);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		fetch("https://backend.sod3.eu/show-results/")
			.then((response) => {
				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
				}
				return response.json();
			})
			.then((data) => setSkusWithLocations(data))
			.catch((error) => {
				console.error("There was a problem with the fetch operation:", error);
				setError(error.message);
			});
	}, []);

	if (error) {
		return (
			<Box width="80%" position="absolute" top="0" right="10" mt={5}>
				<div>Error: {error}</div>
			</Box>
		);
	}

	return (
		<Box width="80%" position="absolute" top="0" right="10" mt={5}>
			<table>
				<thead>
					<tr>
						<th>SKU</th>
						<th>Old Location</th>
						<th>New Location</th>
					</tr>
				</thead>
				<tbody>
					{skusWithLocations.map((sku, index) => (
						<tr key={index}>
							<td>{sku.sku_id}</td>
							<td>{sku.old_location}</td>
							<td>{sku.new_location}</td>
						</tr>
					))}
				</tbody>
			</table>
		</Box>
	);
};

export default ResultsPage;
