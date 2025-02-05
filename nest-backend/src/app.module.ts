import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { OrdersModule } from './orders/orders.module';
import { Order } from './orders/order.entity';

@Module({
  imports: [
    // Load konfigurasi dari .env
    ConfigModule.forRoot({
      isGlobal: true, // Agar bisa diakses di seluruh aplikasi
    }),

    // Konfigurasi koneksi ke PostgreSQL menggunakan variabel .env
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: 'postgres',
        host: configService.get<string>('DB_HOST'),
        port: configService.get<number>('DB_PORT'),
        username: configService.get<string>('DB_USERNAME'),
        password: configService.get<string>('DB_PASSWORD'),
        database: configService.get<string>('DB_DATABASE'),
        entities: [Order],
        synchronize: configService.get<boolean>('DB_SYNCHRONIZE') === true,
      }),
    }),

    OrdersModule,
  ],
})
export class AppModule {}
