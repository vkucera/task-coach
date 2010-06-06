//
//  ItemParser.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "Items.h"

@interface ItemParser : NSObject
{
	BaseItem *current;
	NSMutableArray *stack;
	NSInteger count;
}

- init;
- (BaseItem *)parse:(const char *)format;

@end
