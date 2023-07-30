import React from 'react';
import QRCodeSVG from 'qrcode.react';

const QRCodeGenerator: React.FC<QRCodeGeneratorProps> = ({ url }) => {
  return (
    <div>
      <QRCodeSVG value={url} size="200" renderAs="svg" />
    </div>
  );
};

export default QRCodeGenerator;
