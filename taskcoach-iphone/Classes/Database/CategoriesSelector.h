//
//  CategoriesSelector.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

@interface CategoriesSelector : NSObject
{
	NSMutableArray *clauses;
}

- initWithId:(NSInteger)catId;
- (NSString *)clause;

@end
