//
//  Category.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "DomainObject.h"

@interface Category : DomainObject
{
	NSInteger taskCount;
}

- (NSInteger)count;

@end
