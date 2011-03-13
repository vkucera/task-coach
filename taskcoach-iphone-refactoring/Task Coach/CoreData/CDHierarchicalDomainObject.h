//
//  CDHierarchicalDomainObject.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>
#import "CDDomainObject.h"

@class CDHierarchicalDomainObject;

@interface CDHierarchicalDomainObject : CDDomainObject {
@private
}
@property (nonatomic, retain) NSDate * creationDate;
@property (nonatomic, retain) CDHierarchicalDomainObject * parent;
@property (nonatomic, retain) NSSet* children;

@end
