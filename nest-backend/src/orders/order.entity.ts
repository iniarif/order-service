// nest-backend/src/orders/order.entity.ts
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

@Entity()
export class Order {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  customerName: string;

  @Column()
  product: string;

  @Column('decimal')
  amount: number;

  @CreateDateColumn()
  created_at: Date;
}
