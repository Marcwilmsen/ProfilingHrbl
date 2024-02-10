import { Box } from "@chakra-ui/react";

const MasterAreaOne: React.FC = () => {
	return (
		<>
			<Box width="80%" position="absolute" top="0" right="10" mt={5}>
				<iframe
					src="https://grafana.sod3.eu/public-dashboards/a2c5d1575cfa4a67a577571a81522e7b"
					width="100%"
					height="1200"
					title="Grafana Dashboard"
				></iframe>
			</Box>
		</>
	);
};

export default MasterAreaOne;
