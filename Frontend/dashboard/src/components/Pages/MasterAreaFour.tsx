import { Box } from "@chakra-ui/react";

const MasterAreaOne: React.FC = () => {
	return (
		<>
			<Box width="80%" position="absolute" top="0" right="10" mt={5}>
				<iframe
					src="https://grafana.sod3.eu/public-dashboards/04a52b7b022340ff9e35d8a2ac5198d3"
					width="100%"
					height="1200"
					title="Grafana Dashboard"
				></iframe>
			</Box>
		</>
	);
};

export default MasterAreaOne;
