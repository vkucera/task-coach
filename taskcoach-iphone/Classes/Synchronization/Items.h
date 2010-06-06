//
//  Items.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

@interface BaseItem : NSObject
{
	NSInteger state;
	NSObject *myValue;
}

@property (nonatomic, readonly) NSObject *value;

- init;
- (void)start;
- (NSNumber *)expect;
- (void)feed:(NSData *)data;
- (void)packValue:(NSObject *)value inData:(NSMutableData *)data;

@end

//===================================================================

@interface IntegerItem : BaseItem
{
}

@end

@interface StringItem : BaseItem
{
	NSInteger length;
}

@end

@interface DataItem : BaseItem
{
	NSInteger count;
}

- initWithCount:(NSInteger)count;

@end

@interface VariableDataItem : BaseItem // XXXFIXME: String should inherit from this
{
	NSInteger length;
}

@end

@interface FixedSizeStringItem : StringItem
{
}

@end

@interface DateItem : FixedSizeStringItem
{
	NSDateFormatter *fmt;
}

@end

@interface CompositeItem : BaseItem
{
	NSMutableArray *myItems;
}

- initWithItems:(NSArray *)items;
- (void)append:(BaseItem *)item;

@end

@interface ListItem : BaseItem
{
	BaseItem *myItem;
	NSInteger count;
}

- initWithItem:(BaseItem *)item;
- (void)append:(BaseItem *)item;

@end
