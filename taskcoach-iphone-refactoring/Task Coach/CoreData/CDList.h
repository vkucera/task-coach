//
//  CDList.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class CDDomainObject, CDFile;

@interface CDList : NSManagedObject {
@private
}
@property (nonatomic, retain) NSString * name;
@property (nonatomic, retain) NSSet* objects;
@property (nonatomic, retain) CDFile * file;

@end
