import { Box } from "@chakra-ui/react";

const Analytics: React.FC = () => {
	return (
		<>
			<Box width="80%" position="absolute" top="0" right="10" mt={5}>
				<iframe
					src="https://grafana.sod3.eu/public-dashboards/f7f7ed611bfe46cfb72d74f253bcf16c"
					width="100%"
					height="1200"
					title="Grafana Dashboard"
				></iframe>
			</Box>
		</>
	);
};

export default Analytics;
