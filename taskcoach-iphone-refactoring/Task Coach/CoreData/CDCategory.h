//
//  CDCategory.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>
#import "CDHierarchicalDomainObject.h"

@class CDTask;

@interface CDCategory : CDHierarchicalDomainObject {
@private
}
@property (nonatomic, retain) NSSet* task;

@end
