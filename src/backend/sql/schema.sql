create table users (
    id int auto_increment primary key,
    username varchar(50) unique not null,
    email varchar(100) unique not null,
    password_hash varchar(255) not null,
    role enum('customer', 'manager') not null default 'customer'
);

create table books (
    id int auto_increment primary key,
    title varchar(200) not null,
    author varchar(200) not null,
    buy_price decimal(10,2) not null,
    rent_price decimal(10,2) not null
);

create table orders (
    id int auto_increment PRIMARY KEY,
    user_id int not null,
    status enum('Pending','Paid') not null default 'Pending',
    created_at timestamp default current_timestamp,
    foreign key (user_id) references users(id)
);

create table order_items (
    id int auto_increment PRIMARY KEY,
    order_id int not null,
    book_id int not null,
    type enum('buy','rent') not null,
    price DECIMAL(10,2) not null,
    foreign key (order_id) references orders(id),
    foreign key (book_id) references books(id)
);